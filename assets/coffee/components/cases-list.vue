<template>
  <div class="md-card-list">
    <div v-repeat="cases | filterBy filterKey" class="md-card">
      <div class="md-card-body--padded">
        <a href="{{baseUrl}}/{{display_name}}" class="md-item">
          <div v-show="events.length" class="md-item-icon">
            <div class="cases-indicator"></div>
          </div>

          <div class="md-item-label">{{display_name}}</div>

          <div v-show="assignee.$oid == user_id" class="tag">Assigned</div>
        </a>

        <div class="md-item-subtitle">
          <a href="{{baseUrl}}/{{display_name}}/variants">Variants</a> |
          <span>{{created_at.$date | fromNow}}</span> |
          <span>{{status}}</span>
        </div>
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

      isUpdated: (date) ->
        diff = -moment(date).diff()  # milliseconds
        hh = Math.floor diff / 1000 / 60 / 60  # hours

        if hh < 48
          return yes
        else
          return no

    data: ->
      return {
        baseUrl: ''
        filterKey: ''
        cases: []
        url: ''
        user_id: ''
      }
</script>
