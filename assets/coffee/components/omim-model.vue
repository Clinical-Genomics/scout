<template>
  <span title="{{entry.inheritance_human}}">{{entry.inheritance}}</span>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      if @mim
        superagent.get "/api/v1/omim/inheritance/#{@mim}", (res) =>
          @entry = JSON.parse(res.text)

    data: ->
      return {
        mim: ''
        entry:
          inheritance: 'unknown'
          inheritance_human: ''
      }
</script>
