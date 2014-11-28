<template>
  <textarea v-if="isEditing"
            v-model="content"
            class="markdown-editor-input">
  </textarea>
  <div v-html="html" v-if="!isEditing" class="markdown-editor-html"></div>

  <div class="markdown-editor-toggle">
    <span v-on="click:save" v-if="isEditing">Save</span>
    <span v-on="click:edit" v-if="!isEditing">Edit</span>
  </div>
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

      update: ->
        superagent
          .post "/api/v1/markdown"
          .send { markdown: @content }
          .end (res) =>
            if res.ok
              @html = res.body.html
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
