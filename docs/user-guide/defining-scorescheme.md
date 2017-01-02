# Score scheme

How to score a variant is defined in a .ini file wich is written in a specific way.
The file is divided in sections, the first section is mandatory and is named ```Version```

## Version ##


The file has to start with some meta data that looks like:

```ini
[Version]
		version = 0.1
		name = rank_model_test
```

This is important so the user can backtrack which file that was used for a specific analysis.

## Categories ##


The Score is built by adding scores from different functions where each function has to belong to a category.
The idea with this is that one might not always want to score each function individually, for example if we look at allele frequencies we are most interested in that any of the frequencies are above a certain threshold.
If one frequency is low and another high we just want to use the score for the high frequency.

A category has a name and a category rule, the different rules are ```min, max, sum```.

so this section could look like:

```ini
[Categories]
	[[allele_frequency]]
		category_aggregation = min

 [[Protein_prediction]]
	 category_aggregation = sum
```

## Score functions ##

The following sections in the file will represent score functions. Each function has variables
to describe what field in the vcf file that is used, which category it belongs to, what data type we could expect, how the annotation is separated and what the rule is if there are multiple annotations.

Example:

```ini
[FILTER]
	field = FILTER
	data_type = string
	category = Variant_call_quality_filter
	record_rule = min
	separators = ';',
	description = The filters for the variant
```

so the mandatory sections are:

```
field = #Any of the vcf fields
data_type = # 'integer','float','flag','character','string'
category = # Any of the categories described above
record_rule = # min, max
separators = # A list of separators
```

If field is ```INFO``` we also have to describe what ```INFO```-key to use with

```ini
info_key = # Any of the info keys
```
