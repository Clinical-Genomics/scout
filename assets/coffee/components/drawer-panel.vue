<template>
  <div class="drawer-panel-aside {{side}}"
       v-class="'is-showing': visible">
    <content></content>
  </div>

  <div v-on="click: hide" class="drawer-panel-overlay"></div>
</template>

<script lang="coffee">
  module.exports =
    paramAttributes: ['side']
    methods:
      show: ->
        @visible = yes

      hide: ->
        @visible = no

      toggle: ->
        @visible = not @visible

    data: ->
      return {
        visible: no
        side: 'left'
      }
</script>
