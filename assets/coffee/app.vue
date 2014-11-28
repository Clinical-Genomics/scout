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

      testMkd: ->
        superagent
          .post "/api/v1/markdown"
          .send { markdown: "**Robin** Andeer" }
          .end (res) =>
            if res.ok
              @html = res.body.html
            else
              @html = "Didn't work..."

    data: ->
      message: null
      html: null

    components:
      'drawer-panel': require './components/drawer-panel.vue'
      'core-icon': require './components/core-icon.vue'
      'cases-list': require './components/cases-list.vue'
      'omim-model': require './components/omim-model.vue'
      'omim-summary': require './components/omim-summary.vue'
</script>
