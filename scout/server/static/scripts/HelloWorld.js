import React from 'react';
import './style/HelloWorld.style.css';
import {motion} from 'framer-motion';
import pill from "./assets/test-image.png";

class HelloWorld extends React.Component {
	render() {
		return (
			<div className="loadingAnimation">
				hi
				<img src={pill}/>
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
