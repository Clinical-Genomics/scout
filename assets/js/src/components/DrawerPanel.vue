<style>
  .drawer-panel {
    position: relative;
  }

  .drawer-panel-overlay {
    /* covers the entire container (usually window) */
    position: fixed;
    height: 100%;
    width: 100%;

    /* should be ontop of everything but the drawer */
    z-index: 2;

    /* starts out pushed out of the way and invisible */
    top: 0;
    left: -100%;
    background-color: rgba(0, 0, 0, 0);

    /* fade in when drawer is summoned */
    transition: background-color 250ms,
                left 0s 250ms cubic-bezier(.55, 0, .1, 1);
  }

  .drawer-panel-aside {
    /* add some extra distance to overlay */
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, .18),
                0 4px 15px 0 rgba(0, 0, 0, .15);

    /* coveres the height of the container */
    position: fixed;
    top: 0;
    height: 100%;

    /* fixed but min-width (flex: 0) */
    width: 25rem;

    /* starts out pushed out of view to the left */
    transition: all 250ms cubic-bezier(.55, 0, .1, 1);

    /* should be ontop of everything else pretty much */
    z-index: 3;

    /* scrollable */
    overflow-y: auto;
    padding-bottom: 1rem;

    background-color: #fff;
  }

  .drawer-panel-aside.is-showing + .drawer-panel-overlay {
    /* ... and this activates the overlay as well */
    background-color: rgba(0, 0, 0, .54);

    /* slide in from the left with drawer */
    left: 0;

    /* update transition to make it dissapear quicker than it appeared */
    transition: background-color 400ms;
  }

  .drawer-panel-aside.right {
    /* hide out of view on small screens (+ clear drop shadow) */
    right: -26rem;
  }

  .drawer-panel-aside.right.is-showing {
    /* slide in from the right when summoned */
    right: 0;
  }

  .drawer-panel-aside.left {
    /* hide out of view on small screens (+ clear drop shadow) */
    left: -26rem;
  }

  .drawer-panel-aside.left.is-showing {
    /* slide in from the left when summoned */
    left: 0;
  }
</style>

<template>
  <div class="drawer-panel">
    <div class="drawer-panel-aside"
         v-bind:class="[{ 'is-showing': visible }, side]">
      <slot></slot>
    </div>

    <div v-on:click="hide" class="drawer-panel-overlay"></div>
  </div>
</template>

<script>
  export default {
    props: {
      side: { type: String, default: 'left' },
      visible: { type: Boolean, default: false }
    },

    methods: {
      hide () {
        this.$emit('hide')
      },
      toggle () {
        this.visible = !this.visible
      }
    }
  }
</script>
