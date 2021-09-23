import React, { useEffect, useState } from 'react'
import { getCaseReport } from 'services/ScoutApi'
import ReactPDF, { Page, Text, View, Document, StyleSheet, Font } from '@react-pdf/renderer'

const styles = StyleSheet.create({
  body: {
    paddingTop: 35,
    paddingBottom: 65,
    paddingHorizontal: 35,
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    fontFamily: 'Oswald',
  },
  intro: {
    backgroundColor: '#f2f2f2',
    padding: 30,
  },
  author: {
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 40,
  },
  subtitle: {
    fontSize: 18,
    margin: 12,
    fontFamily: 'Oswald',
  },
  text: {
    margin: 12,
    fontSize: 14,
    textAlign: 'justify',
    fontFamily: 'Times-Roman',
  },
  image: {
    marginVertical: 15,
    marginHorizontal: 100,
  },
  header: {
    fontSize: 12,
    marginBottom: 20,
    textAlign: 'center',
    color: 'grey',
  },
  pageNumber: {
    position: 'absolute',
    fontSize: 12,
    bottom: 30,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: 'grey',
  },
})

Font.register({
  family: 'Oswald',
  src: 'https://fonts.gstatic.com/s/oswald/v13/Y_TKV6o8WovbUd3m_X9aAA.ttf',
})

export const CaseReportPDF = () => {
  const [report, setReport] = useState<any>()
  const today = new Date()

  useEffect(() => {
    getCaseReport()
      .then((response: any) => {
        setReport(response.data.case)
      })
      .catch((error) => {
        console.log(error)
      })
  }, [])
  return report ? (
    <Document>
      <Page size="A4" style={styles.body}>
        <Text style={styles.header} fixed>
          Generated {today.toISOString().slice(0, 10)} at {today.toTimeString().slice(0, 8)}
        </Text>
        <Text style={styles.title}>{report.display_name} REPORT</Text>
        <Text style={styles.author}>Scout - Clinical Genomics</Text>
        <Text style={styles.subtitle}>Status {report.status.toUpperCase()}</Text>
        <Text style={styles.text}>
          Created {new Date(report.created_at).toISOString().slice(0, 10)}
        </Text>
        <Text style={styles.text}>
          Last updated {new Date(report.updated_at).toISOString().slice(0, 10)}
        </Text>
        <View style={styles.intro}>
          {report.individuals.map((individual: any) => (
            <Text key={individual.display_name}>
              {individual.display_name}, {individual.sex_human}, {individual.phenotype_human},
              {individual.analysis_type}, {individual.predicted_ancestry},
              {individual.confirmed_parent || 'N/A'}
            </Text>
          ))}
          {report.comments ? (
            report.comments?.map((comment: any) => <Text key={comment}>{comment}</Text>)
          ) : (
            <Text>No comments available for this case</Text>
          )}
        </View>
        <View style={styles.intro}>
          {report.panels.map((panel: any) => {
            return panel.is_default ? (
              <Text key={panel.display_name}>
                {panel.display_name}, {panel.version}, {panel.nr_genes}
              </Text>
            ) : (
              <></>
            )
          })}
        </View>
      </Page>
    </Document>
  ) : (
    <Document>
      <Page size="A4" style={styles.body}>
        <Text style={styles.subtitle}>NO REPORT FOUND</Text>
      </Page>
    </Document>
  )
}
