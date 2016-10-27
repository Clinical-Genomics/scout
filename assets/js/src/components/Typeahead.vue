<style>
  .typeahead {
    border-bottom: 2px solid rgba(0, 0, 0, 0.2);
  }

  .typeahead-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .typeahead-list-item {
    padding: .5rem 1rem;
    white-space: nowrap;
    overflow-x: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
  }

  .typeahead-list-item:hover {
    background: rgba(0, 0, 0, .1);
  }

  .typeahead-list-item:active {
    background: rgba(0, 0, 0, .15);
  }
</style>

<template>
  <div class="typeahead">
    <div class="md-card-footer layout">
      <input type="text" v-model.trim="query" placeholder="HPO query">
      <button class="md-button-flat" v-on:click="send">Submit</button>
    </div>
    <ul class="typeahead-list" v-show="queryLongEnough">
      <li class="typeahead-list-item" v-on:click="selectItem(item)" v-for="item in results">
        {{ item.id }}: {{ item.title }}
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    props: ['url'],
    data () {
      return {
        query: null,
        selected: null,
        results: [],
        isWaiting: false
      }
    },
    watch: {
      query: function(value) {
        if (value.length === 0) {
          this.selected = null
        } else if (!this.isWaiting && this.queryLongEnough) {
          this.updateResults()
          this.isWaiting = true
          setTimeout(() => {
            this.isWaiting = false
          }, 300)
        }
      },
    },
    methods: {
      selectItem (item) {
        this.selected = item
        this.query = `${item.id}: ${item.title}`
      },
      send () {
        if (this.query.startsWith('HP:') && this.query.length === 10) {
          this.$emit('send', this.query)
        } else {
          this.$emit('send', this.selected.id)
        }
      },
      updateResults () {
        superagent
          .get('/api/v1/hpo-terms')
          .query({ query: this.query })
          .end((err, res) => {
            if (err || !res.ok) {
              console.log("HPO query failed")
            } else {
              this.results = res.body
            }
          })
      },
    },
    computed: {
      queryLongEnough () {
        if (this.query) {
          return this.query.length > 3
        } else {
          return false
        }
      },
    },
  }
</script>
