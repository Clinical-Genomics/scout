<template>
  <span>{{entry.models | join ,}}</span>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      if @url
        superagent.get @url, (res) =>
          @entry = JSON.parse(res.text)

          if @entry.models.length is 0
            @entry.models = ['unknown']

    data: ->
      return {
        url: ''
        entry:
          models: ['loading...']
      }

    filters:
      join: (list, separator) ->
        return list.join(separator)
</script>
