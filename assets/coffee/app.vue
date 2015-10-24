<script lang="coffee">
  module.exports =
    methods:
      showDrawer: ->
        @$.drawer.show()

      showFilters: ->
        @$.filters.show()

      onVariantRankChange: (e) ->
        superagent
          .put "/api/v1#{location.pathname}/manual_rank"
          .send { manual_rank: @variantRank }
          .end (res) =>
            if res.ok
              @message = 'Manual variant rank updated!'
            else
              @message = 'Manual variant rank update failed.'

      showModal: ->
        @$.modal.show()

      hideModal: ->
        @$.modal.hide()

      updateSynopsis: (markdown) ->
        superagent
          .put "/api/v1#{location.pathname}/synopsis"
          .send { synopsis: markdown }
          .end (res) ->
            if res.ok
              @message = 'Synopsis updated!'
            else
              @message = 'Synopsis update failed.'

    computed:
      mimNumber: ->
        return @$.omim.mimNumber

    data: ->
      message: null
      html: null

    ready: ->
      # prevent FOUC
      # ref: http://en.wikipedia.org/wiki/Flash_of_unstyled_content
      body = document.getElementsByTagName('body')[0]
      body.classList.remove('unresolved')

    components:
      'drawer-panel': require './components/drawer-panel.vue'
      'core-icon': require './components/core-icon.vue'
      'markdown-editor': require './components/markdown-editor.vue'
      'md-modal': require './components/md-modal.vue'
</script>
