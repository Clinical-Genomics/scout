import logging
import urllib
from pprint import pprint as pp

from flask import url_for
from flask_login import current_user
from flask_mail import Message

from scout.server.extensions import mail as ex_mail
from scout.server.links import external_primer_order_link

from .controllers import variant as variant_controller

LOG = logging.getLogger(__name__)


class MissingVerificationRecipientError(Exception):
    pass


def variant_verification(
    store,
    institute_id,
    case_name,
    variant_id,
    sender,
    variant_url,
    order,
    comment,
    url_builder=None,
    mail=None,
    user_obj=None,
):
    """Sand a verification email and register the verification in the database

    Args:
        store(scout.adapter.MongoAdapter)
        institute_obj(dict): an institute object
        case_obj(dict): a case object
        user_obj(dict): a user object
        variant_obj(dict): a variant object (snv or sv)
        sender(str): current_app.config['MAIL_USERNAME']
        variant_url(str): the complete url to the variant (snv or sv), a link that works from outside scout domain.
        order(str): False == cancel order, True==order verification
        comment(str): sender's entered comment from form
        url_builder(flask.url_for): for testing purposes, otherwise test verification email fails because out of context
    """
    url_builder = url_builder or url_for
    mail = mail or ex_mail
    user_obj = user_obj or store.user(current_user.email)

    data = variant_controller(
        store,
        institute_id,
        case_name,
        variant_id=variant_id,
        add_case=True,
        add_other=False,
        get_overlapping=False,
        add_compounds=False,
    )
    variant_obj = data["variant"]
    case_obj = data["case"]
    institute_obj = data["institute"]
    pp(variant_obj)
    recipients = institute_obj["sanger_recipients"]
    if len(recipients) == 0:
        raise MissingVerificationRecipientError()

    view_type = None
    email_subject = None
    category = variant_obj.get("category", "snv")
    display_name = variant_obj.get("display_name")
    chromosome = variant_obj["chromosome"]
    position = variant_obj["position"]
    end_chrom = variant_obj.get("end_chrom", chromosome)
    chr_position = (
        ":".join([chromosome, str(variant_obj["position"])]) if category in ["snv"] else "-"
    )
    breakpoint_1 = (
        ":".join([chromosome, str(variant_obj["position"])])
        if category in ["sv", "cancer_sv"]
        else "-"
    )
    breakpoint_2 = (
        ":".join([end_chrom, str(variant_obj.get("end"))])
        if category in ["sv", "cancer_sv"]
        else "-"
    )
    variant_size = variant_obj.get("length")
    panels = ", ".join(variant_obj.get("panels", []))
    gene_identifiers = [
        str(ident) for ident in variant_obj.get("hgnc_symbols", variant_obj.get("hgnc_ids", []))
    ]
    hgnc_symbol = ", ".join(gene_identifiers)
    email_subj_gene_symbol = None
    if len(gene_identifiers) > 3:
        email_subj_gene_symbol = " ".join([str(len(gene_identifiers)) + "genes"])
    else:
        email_subj_gene_symbol = hgnc_symbol

    gtcalls = [
        "<li>{}: {}</li>".format(sample_obj["display_name"], sample_obj["genotype_call"])
        for sample_obj in variant_obj["samples"]
    ]
    tx_changes = []
    external_primer_link = ""

    if category == "snv":  # SNV
        view_type = "variant.variant"
        tx_changes = []

        external_primer_link = external_primer_order_link(variant_obj, case_obj["genome_build"])

        for gene_obj in variant_obj.get("genes", []):
            for tx_obj in gene_obj["transcripts"]:
                # select refseq transcripts as "primary"
                if not tx_obj.get("refseq_id"):
                    continue

                for refseq_id in tx_obj.get("refseq_identifiers"):
                    transcript_line = []
                    transcript_line.append(gene_obj.get("hgnc_symbol", gene_obj["hgnc_id"]))

                    transcript_line.append("-".join([refseq_id, tx_obj["transcript_id"]]))
                    if "exon" in tx_obj:
                        transcript_line.append("".join(["exon", tx_obj["exon"]]))
                    elif "intron" in tx_obj:
                        transcript_line.append("".join(["intron", tx_obj["intron"]]))
                    else:
                        transcript_line.append("intergenic")
                    if "coding_sequence_name" in tx_obj:
                        transcript_line.append(urllib.parse.unquote(tx_obj["coding_sequence_name"]))
                    else:
                        transcript_line.append("")
                    if "protein_sequence_name" in tx_obj:
                        transcript_line.append(
                            urllib.parse.unquote(tx_obj["protein_sequence_name"])
                        )
                    else:
                        transcript_line.append("")
                    if "strand" in tx_obj:
                        transcript_line.append(tx_obj["strand"])
                    else:
                        transcript_line.append("")
                    if refseq_id in gene_obj["common"]["primary_transcripts"]:
                        transcript_line.append("<b>primary</b>")
                    else:
                        transcript_line.append("")

                    tx_changes.append("<li>{}</li>".format(":".join(transcript_line)))

    else:  # SV
        view_type = "variant.sv_variant"
        display_name = "_".join([breakpoint_1, variant_obj.get("sub_category").upper()])

    # body of the email
    html = verification_email_body(
        case_name=case_obj["display_name"],
        url=variant_url,  # this is the complete url to the variant, accessible when clicking on the email link
        display_name=display_name,
        category=category.upper(),
        subcategory=variant_obj.get("sub_category").upper(),
        breakpoint_1=breakpoint_1,
        breakpoint_2=breakpoint_2,
        chr_position=chr_position,
        hgnc_symbol=hgnc_symbol,
        panels=panels,
        gtcalls="".join(gtcalls),
        tx_changes="".join(tx_changes) or "Not available",
        name=user_obj["name"].encode("utf-8"),
        comment=comment,
        external_primer_link=external_primer_link,
    )

    # build a local the link to the variant to be included in the events objects (variant and case) created in the event collection.
    local_link = url_builder(
        view_type,
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
        variant_id=variant_obj["_id"],
    )

    if order == "True":  # variant verification should be ordered
        # pin variant if it's not already pinned
        if case_obj.get("suspects") is None or variant_obj["_id"] not in case_obj["suspects"]:
            store.pin_variant(institute_obj, case_obj, user_obj, local_link, variant_obj)

        email_subject = "SCOUT: validation of {} variant {}, ({})".format(
            category.upper(), display_name, email_subj_gene_symbol
        )
        store.order_verification(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=local_link,
            variant=variant_obj,
        )

    else:  # variant verification should be cancelled
        email_subject = "SCOUT: validation of {} variant {}, ({}), was CANCELLED!".format(
            category.upper(), display_name, email_subj_gene_symbol
        )
        store.cancel_verification(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=local_link,
            variant=variant_obj,
        )

    kwargs = dict(
        subject=email_subject,
        html=html,
        sender=sender,
        recipients=recipients,
        # cc the sender of the email for confirmation
        cc=[user_obj["email"]],
    )

    message = Message(**kwargs)
    # send email using flask_mail
    mail.send(message)


def verification_email_body(
    case_name,
    url,
    display_name,
    category,
    subcategory,
    chr_position,
    breakpoint_1,
    breakpoint_2,
    hgnc_symbol,
    panels,
    gtcalls,
    tx_changes,
    name,
    comment,
    external_primer_link,
):
    """
    Builds the html code for the variant verification emails (order verification and cancel verification)

    Args:
        case_name(str): case display name
        url(str): the complete url to the variant, accessible when clicking on the email link
        display_name(str): a display name for the variant
        category(str): category of the variant
        subcategory(str): sub-category of the variant
        chr_position(str): chromosomal position for SNVs (format is 'chr:start')
        breakpoint_1(str): breakpoint 1 (format is 'chr:start')
        breakpoint_2(str): breakpoint 2 (format is 'chr:stop')
        hgnc_symbol(str): a gene or a list of genes separated by comma
        panels(str): a gene panel of a list of panels separated by comma
        gtcalls(str): genotyping calls of any sample in the family
        tx_changes(str): amino acid changes caused by the variant, only for snvs otherwise 'Not available'
        name(str): user_obj['name'], uft-8 encoded
        comment(str): sender's comment from form
        external_primer_link(str): optional URL to an external primer ordering page

    Returns:
        html(str): the html body of the variant verification email

    """
    external_primer_link_html = ""
    if external_primer_link:
        external_primer_link_html = f'<li><a href="{external_primer_link}">Order primers</a>'

    html = """
       <ul>
         <li>
           <strong>Case {case_name}</strong>: <a href="{url}">{display_name}</a>
         </li>
         <li><strong>Variant type</strong>: {category} ({subcategory})
         <li><strong>Chromosomal position</strong>: {chr_position}</li>
         <li><strong>Breakpoint 1</strong>: {breakpoint_1}</li>
         <li><strong>Breakpoint 2</strong>: {breakpoint_2}</li>
         <li><strong>HGNC symbols</strong>: {hgnc_symbol}</li>
         <li><strong>Gene panels</strong>: {panels}</li>
         <li><strong>GT call</strong></li>
         {gtcalls}
         <li><strong>Amino acid changes</strong></li>
         {tx_changes}
         {external_primer_link_html}
         <li><strong>Comment</strong>: {comment}</li>
         <li><strong>Ordered by</strong>: {name}</li>
       </ul>
    """.format(
        case_name=case_name,
        url=url,
        display_name=display_name,
        category=category,
        subcategory=subcategory,
        chr_position=chr_position,
        breakpoint_1=breakpoint_1,
        breakpoint_2=breakpoint_2,
        hgnc_symbol=hgnc_symbol,
        panels=panels,
        gtcalls=gtcalls,
        tx_changes=tx_changes,
        name=name,
        comment=comment,
        external_primer_link_html=external_primer_link_html,
    )

    return html
