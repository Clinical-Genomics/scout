<style>
  .typeahead-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .typeahead-list-item,
  .bs-typeahead-list-item {
    white-space: nowrap;
    overflow-x: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
  }

  .typeahead-list-item {
    padding: .5rem 1rem;
  }

  .typeahead-list-item:hover,
  .bs-typeahead-list-item:hover {
    background: rgba(0, 0, 0, .1);
  }

  .typeahead-list-item:active,
  .bs-typeahead-list-item:active {
    background: rgba(0, 0, 0, .15);
  }

  .bs-typeahead-list-item {

  }
</style>

<template>
  <div class="typeahead">
    <div v-if="isBootstrap">
      <div class="panel panel-default">
        <div class="panel-body">
          <form v-on:submit="send">
            <div class="row">
              <div class="col-xs-8">
                <input id="typeahead-input" type="text" v-model.trim="query" class="form-control" placeholder="Search" @keyup.down="highlightNext" @keyup.up="highlightPrev">
              </div>
              <div class="col-xs-4">
                <button type="submit" class="btn btn-default form-control">Submit</button>
              </div>
            </div>
          </form>
        </div>
        <ul class="list-group" v-show="queryLongEnough">
          <li class="list-group-item bs-typeahead-list-item" v-on:click="selectItem(item)" v-for="(item, index) in results">
            <span v-if="index == highlightIndex" class="badge">*</span>
            {{ item.id }}: {{ item.title }}
          </li>
        </ul>
      </div>
    </div>
    <div v-if="!isBootstrap">
      <form class="md-card-footer layout" v-on:submit="send">
        <input type="text" v-model.trim="query" placeholder="search query">
        <button type="submit" class="md-button-flat">Submit</button>
      </form>
      <ul class="typeahead-list" v-show="queryLongEnough">
        <li class="typeahead-list-item" v-on:click="selectItem(item)" v-for="item in results">
          {{ item.id }}: {{ item.title }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
  export default {
    props: ['url', 'bootstrap'],
    data () {
      return {
        query: null,
        selected: null,
        results: [],
        isWaiting: false,
        highlighted: null,
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
        document.getElementById("typeahead-input").focus();
      },
      send (event) {
        event.preventDefault()
        if (this.selected) {
          this.$emit('send', {
            query: this.query,
            id: this.selected.id
          })
        } else {
          this.selectItem(this.highlighted)
        }
      },
      updateResults () {
        superagent
          .get(this.url)
          .query({ query: this.query })
          .end((err, res) => {
            if (err || !res.ok) {
              console.log("Search query failed")
            } else {
              this.results = res.body.results
            }
          })
      },
      highlightNext () {
        if (this.results.length > 0) {
          if (this.highlighted) {
            this.highlighted = this.results[this.highlightIndex + 1]
          } else {
            this.highlighted = this.results[0]
          }
        }
      },
      highlightPrev () {
        if (this.results.length > 0) {
          if (this.highlighted) {
            this.highlighted = this.results[this.highlightIndex - 1]
          } else {
            this.highlighted = this.results[0]
          }
        }
      },
    },
    computed: {
      queryLongEnough () {
        if (this.query) {
          return this.query.length >= 3
        } else {
          return false
        }
      },
      isBootstrap () {
        return this.bootstrap === 'yes'
      },
      highlightIndex () {
        if (this.highlighted) {
          return this.results.indexOf(this.highlighted)
        } else {
          return -1
        }
      },
    },
  }
</script>
