<script lang="coffee">
  module.exports =
    methods:
      showDrawer: ->
        @$.drawer.show()

      onChange: (e) ->
        superagent
          .put "/api/v1#{location.pathname}/status"
          .send { status: @selected }
          .end (res) =>
            if res.ok
              @message = 'Status changed!'
            else
              @message = 'Status update failed.'

      updateSynopsis: (markdown) ->
        superagent
          .put "/api/v1#{location.pathname}/synopsis"
          .send { synopsis: markdown }
          .end (res) ->
            if res.ok
              @message = 'Synopsis updated!'
            else
              @message = 'Synopsis update failed.'

    data: ->
      message: null
      html: null

    components:
      'drawer-panel': require './components/drawer-panel.vue'
      'core-icon': require './components/core-icon.vue'
      'cases-list': require './components/cases-list.vue'
      'omim-model': require './components/omim-model.vue'
      'omim-summary': require './components/omim-summary.vue'
      'markdown-editor': require './components/markdown-editor.vue'
</script>
