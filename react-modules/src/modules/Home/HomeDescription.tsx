import { Typography } from 'antd'
import React from 'react'
import styles from './HomeDescription.module.css'

export const HomeDescription = () => (
	<Typography className={styles.body}>
		Scout allows you to browse VCFs in a web browser, identify compound pairs, and solve cases as a
		team.
	</Typography>
)
