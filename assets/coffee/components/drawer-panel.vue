<template>
  <div class="drawer-panel-aside {{visible ? 'is-showing' : ''}}">
    <content></content>
  </div>

  <div v-on="click: hide" class="drawer-panel-overlay"></div>
</template>

<script lang="coffee">
  module.exports =
    methods:
      show: ->
        @visible = yes

      hide: ->
        @visible = no

      toggle: ->
        @visible = not @visible

    data: ->
      return { visible: no }
</script>
