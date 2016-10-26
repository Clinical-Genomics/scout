<script>
  import CoreIcon from './components/CoreIcon.vue'
  import DrawerPanel from './components/DrawerPanel.vue'
  import MarkdownEditor from './components/MarkdownEditor.vue'
  import CoreModal from './components/CoreModal.vue'
  import Typeahead from './components/Typeahead.vue'

  export default {
    name: 'app',

    data () {
      return {
        drawerVisible: false,
        modalVisible: false,
        drawerRightVisible: false,
        modalSecondVisible: false,
        variantRank: null
      }
    },

    mounted () {
      // prevent FOUC
      // ref: http://en.wikipedia.org/wiki/Flash_of_unstyled_content
      let body = document.getElementsByTagName('body')[0]
      body.classList.remove('unresolved')
    },

    methods: {
      updateSynopsis (markdown) {
        superagent
          .put(`/api/v1${location.pathname}/synopsis`)
          .send({ synopsis: markdown })
          .end((res) => {
            if (res.ok) {
              console.log('Synopsis updated!')
            } else {
              console.log('Synopsis update failed.')
            }
          })
      },
      onVariantRankChange (event) {
        superagent
          .put(`/api/v1${location.pathname}/manual_rank`)
          .send({ manual_rank: this.variantRank })
          .end((err, res) => {
            if (err || !res.ok) {
              console.log('Manual variant rank update failed.')
            } else {
              console.log('Manual variant rank updated!')
            }
          })
      },
      showModal () {
        this.modalVisible = true
      },
      hideModal () {
        this.modalVisible = false
      },
      showSecondModal () {
        this.modalSecondVisible = true
      },
      hideSecondModal () {
        this.modalSecondVisible = false
      },
      showDrawer () {
        this.drawerVisible = true
      },
      hideDrawer () {
        this.drawerVisible = false
      },
      showRightDrawer () {
        this.drawerRightVisible = true
      },
      hideRightDrawer () {
        this.drawerRightVisible = false
      }
    },

    components: {
      'core-icon': CoreIcon,
      'drawer-panel': DrawerPanel,
      'markdown-editor': MarkdownEditor,
      'core-modal': CoreModal,
      'typeahead': Typeahead
    }
  }
</script>

<style>
  *, :after, :before {
    box-sizing: border-box;
  }

  body, html {
    height: 100%;
    width: 100%;
    overflow: auto;
    padding: 0;
    margin: 0;
  }

  #app {
    height: inherit;
    width: inherit;
  }
</style>
