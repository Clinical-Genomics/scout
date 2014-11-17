<template>
  <div v-repeat="cases | filterBy filterKey" class="cases-item">

      <a class="cases-item-title" href="{{ baseUrl }}/{{ name }}">
        <div class="cases-item-indicator"></div>
        {{name}}
      </a>

      <div class="cases-item-bonus">

        <a href="{{ baseUrl }}/{{ name }}/variants" class="cases-item-link">
          Variants
        </a>

        <div class="cases-item-date">
          Updated {{created_at.$date | fromNow}}
        </div>

      </div>

  </div>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      superagent.get @url, (res) =>
        @cases = JSON.parse(res.text)

    filters:
      fromNow: (date) ->
        return moment(date).fromNow()

    data: ->
      return {
        baseUrl: ''
        filterKey: ''
        cases: []
        url: ''
      }
</script>
