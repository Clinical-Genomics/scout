<template>
  <div class="md-card-list">
    <div v-repeat="cases | filterBy filterKey" class="md-card">
      <div class="md-card-body--padded">
        <a href="{{baseUrl}}/{{display_name}}" class="md-item">
          <div v-show="events.length" class="md-item-icon">
            <div class="cases-indicator"></div>
          </div>

          <div class="md-item-label">{{display_name}}</div>

          <template v-if="assignee">
            <div v-show="assignee.$oid != user_id" class="tag">Assigned</div>

            <div v-show="assignee.$oid == user_id" class="tag">
              {{user_name}}
            </div>
          </template>
        </a>

        <div class="md-item-subtitle">
          <a href="{{baseUrl}}/{{display_name}}/clinical?{{ default_gene_lists | joinParams gene_lists }}">Clinical variants</a> |
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

      joinParams: (list, param) ->
        if list.length > 1
          return "#{param}=#{list.join("#{param}=&")}"
        else
          # avoid building an empty param variable
          return ''

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
        user_name: ''
      }
</script>
