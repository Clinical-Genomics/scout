<script lang="coffee">
	module.exports =
		methods:
			showDrawer: ->
				@$.drawer.show()

		components:
			'drawer-panel': require './components/drawer-panel.vue'
			'core-icon': require './components/core-icon.vue'
</script>
