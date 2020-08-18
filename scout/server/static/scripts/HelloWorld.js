import React from 'react';
import './style/HelloWorld.style.css';
import {motion} from 'framer-motion';

class HelloWorld extends React.Component {
	render() {
		return (
			<div className="loadingAnimation">
				Hi! I am a tiny React app
				<motion.div
					animate={{
						rotate: 360,
					}}
					transition={{
						duration: 1.5,
						ease: "easeInOut",
						loop: Infinity,
					}}
				/>
			</div>
		);
	}
}

export default HelloWorld;
