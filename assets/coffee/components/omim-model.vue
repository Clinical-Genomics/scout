<template>
  <span title="{{entry.inheritance_human}}">{{entry.inheritance}}</span>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      if @url
        superagent.get @url, (res) =>
          @entry = JSON.parse(res.text)

    data: ->
      return {
        url: ''
        entry:
          inheritance: 'unknown'
          inheritance_human: ''
      }
</script>
