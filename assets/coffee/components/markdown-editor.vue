<template>
  <textarea v-show="isEditing"
            v-model="content"
            class="markdown-editor-input"
            placeholder="Edit synopsis">
  </textarea>
  <div v-html="html" v-show="!isEditing" class="markdown-editor-html"></div>
</template>

<script lang="coffee">
  module.exports =
    ready: ->
      @update()

    methods:
      edit: ->
        @isEditing = yes

      save: ->
        @update()
        @isEditing = no

        if @onSave
          @onSave(@content)

      cancel: ->
        @isEditing = no

      update: ->
        superagent
          .post "/api/v1/markdown"
          .send { markdown: @content }
          .end (res) =>
            if res.ok
              @html = res.body.html or '<h3>Nothing written yet.</h3>'
            else
              @html = "<p>Server error...</p>"

    data: ->
      return {
        isEditing: no
        content: ''
        html: ''
        onSave: null
      }
</script>
