<template>
  <div v-show="!isFound" class="omim-summary-empty">
    No OMIM entry found.
  </div>

  <div class="omim-summary">
    <div v-repeat="entry.other_entities" class="omim-summary-entities">
      {{$value}}
    </div>

    <div v-repeat="entry.phenotypes" class="omim-summary-phenotype">
      <div class="omim-summary-phenotype-item">{{phenotype}}</div>
      <div class="omim-summary-phenotype-item">{{inheritance}}</div>
      <div class="omim-summary-phenotype-item">{{mapping_key}}</div>
    </div>
  </div>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      superagent.get @url, (res) =>
        @entry = JSON.parse(res.text)
        if @entry.gene_symbol
          @isFound = yes

    data: ->
      return {
        url: null
        entry: {}
        isFound: no
      }
</script>
