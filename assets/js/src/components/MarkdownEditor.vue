<style>
  .markdown-editor {
    width: 100%;
    position: relative;
  }

  .markdown-editor-input {
    width: 100%;
    min-height: 15em;
  }

  .markdown-save-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
  }
</style>

<template>
  <div class="markdown-editor">
    <textarea v-show="isEditing"
              v-model="mkdContent"
              class="markdown-editor-input"
              placeholder="Edit synopsis">
    </textarea>
    <div v-html="html" v-show="!isEditing" class="markdown-editor-html"></div>

    <div class="markdown-toolbar">
      <button class="markdown-toolbar-btn" v-show="!isEditing" v-on:click="showEditor">Edit</button>
      <button class="markdown-toolbar-btn" v-show="isEditing" v-on:click="save">Save</button>
      <button class="markdown-toolbar-btn" v-show="isEditing" v-on:click="hideEditor">Cancel</button>
    </div>

  </div>
</template>

<script>
  export default {
    props: {
      content: {
        type: String,
        default: null
      }
    },
    data () {
      return {
        html: '',
        isEditing: false,
        mkdContent: null
      }
    },
    mounted () {
      this.update()
      this.mkdContent = this.content.replace(/(^[ '\^\$\*#&]+)|([ '\^\$\*#&]+$)/g, '')
    },
    methods: {
      showEditor () {
        this.isEditing = true
      },
      hideEditor () {
        this.isEditing = false
      },
      save () {
        this.update()
        this.$emit('hide')
        this.$emit('save', this.mkdContent)
      },
      update () {
        superagent.post("/api/v1/markdown")
                  .send({ markdown: this.mkdContent })
                  .end((err, res) => {
                    if (err || !res.ok) {
                        this.html = "<p>Server error...</p>"
                    } else {
                        this.html = res.body.html || "<h3>Nothing written yet.</h3>"
                    }
                  })
      }
    }
  }
</script>
