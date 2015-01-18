<template>
  <div>Matches expected inheritance model</div>

  <div v-show="isMatching" class="md-badge--success">Yes</div>

  <div v-show="!isMatching" class="md-badge--fail">No</div>
</template>

<script lang="coffee">
  module.exports =
    paramAttributes: ['result', 'url']

    ready: ->
      if @url
        superagent.get @url, (res) =>
          @entry = JSON.parse(res.text)

          if @entry.models.length is 0 or @entry.models[0] is null
            @entry.models = ['unknown']

    computed:
      resultList: ->
        return @result.split ','

      omimModels: ->
        if @entry
          return @entry.models
        else
          return []

      isMatching: ->
        return @resultList == @omimModels

    filters:
      join: (list, separator) ->
        return list.join(separator)

    data: ->
      return {
        url: ''
        result: []
      }
</script>
