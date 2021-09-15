export const windowMatchMedia = () => {
	return (
		window.matchMedia ||
		function () {
			return {
				matches: false,
				addListener: () => null,
				removeListener: () => null,
			}
		}
	)
}
