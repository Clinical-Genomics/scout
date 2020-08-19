import React from 'react';
import './style/HelloWorld.style.css';
import {motion} from 'framer-motion';

class HelloWorld extends React.Component {
	render() {
		return (
			<div className="loadingAnimation">
				<motion.div
					drag
					dragConstraints={{
						top: -250,
						left: -250,
						right: 250,
						bottom: 250,
					}}
				/>
			</div>
		);
	}
}

export default HelloWorld;
