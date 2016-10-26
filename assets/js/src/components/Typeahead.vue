<template>
  <div class="typeahead">
    <input type="text" v-model.trim="query">
    <ul v-show="queryLongEnough">
      <li v-on:click="selectItem(item)" v-for="item in results">{{ item.title }}</li>
    </ul>
    <button v-on:click="send" :disabled="!hasSelected">Submit</button>
  </div>
</template>

<script>
  export default {
    props: ['url'],
    data () {
      return {
        query: null,
        selected: null
      }
    },
    watch: {
      query: (value) => {
        console.log('dioawj')
        if (value.length === 0) {
          console.log('aaaaa')
          this.selected = null
        }
      }
    },
    methods: {
      selectItem (item) {
        this.selected = item
        this.query = item.title
      },
      send () {
        this.$emit('send', this.selected)
      },
    },
    computed: {
      hasSelected () {
        return this.selected !== null
      },
      queryLongEnough () {
        if (this.query) {
          return this.query.length > 3
        } else {
          return false
        }
      },
      results () {
        return [{
          'title': 'Space',
          'id': 'space1'
        }]
      },
    },
  }
</script>
