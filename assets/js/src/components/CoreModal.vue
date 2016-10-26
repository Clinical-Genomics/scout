<template>
  <div class="core-modal">
    <div class="core-modal-window" v-bind:class="{ 'is-showing': visible }">
      <div v-show="title" class="core-modal-header">{{ title }}</div>

      <div class="core-modal-body">
        <slot></slot>
      </div>
    </div>

    <div v-on:click="hide" class="core-modal-overlay"></div>
  </div>
</template>

<script>
  export default {
    props: {
      title: {
        type: String
      },
      visible: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      hide () {
        this.$emit('hide')
      }
    }
  }
</script>

<style>
  .core-modal {
    display: flex;
    align-items: flex-start;
    justify-content: center;

    position: absolute;
    top: 0;
    width: 100%;
  }

  .core-modal-overlay {
    /* covers the entire container (usually window) */
    position: fixed;
    height: 100%;
    width: 100%;

    /* should be ontop of everything but the drawer */
    z-index: 2;
    cursor: pointer;

    top: -100%;
    left: 0;
    background-color: rgba(0, 0, 0, 0);

    /* fade in when drawer is summoned */
    transition: background-color 250ms;
  }

  .core-modal-window {
    /* add some extra distance to overlay */
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, .18),
                0 4px 15px 0 rgba(0, 0, 0, .15);

    display: none;
    margin-top: -100%;
    min-width: 30rem;

    /* should be ontop of everything else pretty much */
    z-index: 3;

    background-color: #fff;
    transition: margin-top .2s;
  }

  .core-modal-window.is-showing {
    display: block;
    margin-top: 0;
  }

  .core-modal-window.is-showing + .core-modal-overlay {
    /* ... and this activates the overlay as well */
    background-color: rgba(0, 0, 0, .54);
    top: 0;
  }

  .core-modal-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, .2);
    background-color: rgba(0, 0, 0, .05);
    font-weight: bold;
  }

  .core-modal-body {
    padding: 0.5rem 1rem;
  }
</style>
