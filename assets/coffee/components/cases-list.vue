<template>
  <div v-repeat="cases | filterBy filterKey" class="cases-item">

    <a class="cases-item-title" href="{{baseUrl}}/{{display_name}}">
      <div class="cases-item-indicator"></div>
      {{display_name}}

      <div v-if="assignee.$oid == user_id" class="tag">Assigned</div>
    </a>

    <div class="cases-item-bonus">

      <a href="{{baseUrl}}/{{display_name}}/variants" class="cases-item-link">
        Variants
      </a>

      <!-- <div class="cases-item-databases">IEM, EP</div> -->

      <div class="cases-item-date">
        Updated {{last_updated.$date | fromNow}}
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
        user_id: ''
      }
</script>
