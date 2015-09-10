<template>
  <div class="md-card-list">
    <div v-repeat="cases | filterBy filterKey" class="md-card">
      <div class="md-card-body--padded">
        <a href="{{baseUrl}}/{{display_name}}" class="md-item">
          <div v-show="events.length" class="md-item-icon">
            <div class="dot-indicator"></div>
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
          <template v-if="is_research">
            <a href="{{baseUrl}}/{{display_name}}/research">Research variants</a>
          </template>
          <template v-if="!is_research">
            <a href="{{baseUrl}}/{{display_name}}/clinical?{{ default_gene_lists | joinParams gene_lists }}">Clinical variants</a>
          </template>
           |
          <span>{{created_at.$date | formatISO}}</span> |
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
      formatISO: (date) ->
        dateObj = new Date(date)
        return dateObj.toISOString().slice(0, 10)

      joinParams: (list, param) ->
        if list.length > 1
          return "#{param}=#{list.join("&#{param}=")}"
        else
          # avoid building an empty param variable
          return ''

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
