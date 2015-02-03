<template>
  <div>Matches expected inheritance model</div>

  <div class="md-badge--{{category}}">{{message}}</div>
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

      isMatching: ->
        for result in @resultList
          for omimModel in @entry.models
            if result.indexOf(omimModel) > -1
              return yes

        return no

      category: ->
        if @entry
          if @entry.models[0] is 'unknown'
            return 'warning'
          else if @isMatching
            return 'success'
          else
            return 'fail'

      message: ->
        if @category is 'warning'
          return 'N/A'
        else if @category is 'success'
          return 'Yes'
        else
          return 'No'

    filters:
      join: (list, separator) ->
        return list.join(separator)

    data: ->
      return {
        url: ''
        result: []
        entry: null
        isMatching: null
      }
</script>
