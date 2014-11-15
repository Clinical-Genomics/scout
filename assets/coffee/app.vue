<script lang="coffee">
	module.exports =
		methods:
			showDrawer: ->
				@$.drawer.show()

		components:
			'drawer-panel': require './components/drawer-panel.vue'
</script>
