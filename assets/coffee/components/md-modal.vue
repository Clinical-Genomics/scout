<template>
  <div class="md-modal" v-class="'is-showing': visible">
    <div v-show="title" class="md-modal-header">{{title}}</div>

    <div class="md-modal-body">
      <content></content>
    </div>
  </div>

  <div v-on="click: hide" class="md-modal-overlay"></div>
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
      return {
        visible: no
      }
</script>
