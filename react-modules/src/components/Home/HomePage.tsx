import React, { useEffect } from 'react'
import ScilifelabLogo from 'assets/SciLifeLab_Logotype_POS.png'
import ScilifelabLogoDark from 'assets/SciLifeLab_Logotype_NEG.png'
import KarolinskaLogoDark from 'assets/ki_logo_neg.png'
import KarolinskaLogo from 'assets/ki_logo_pos.png'
import SwedacLogo from 'assets/swedac.png'
import { connect } from 'react-redux'
import { RootState } from 'domain/rootReducer'
import packageJson from '../../../package.json'
import styles from './HomePage.module.css'
import { setDarkMode as setSettingsAction } from 'domain/settings/slice'
import { HomeDescription } from 'modules/Home/HomeDescription'
import { Card, Divider, Typography } from 'antd'

const mapDispatch = { setDarkMode: setSettingsAction } as const
const mapState = ({ settings }: RootState) => ({ settings } as const)
type Props = ReturnType<typeof mapState> & typeof mapDispatch

function HomePage({ settings, setDarkMode }: Props) {
	const scoutVersion = packageJson.version
	const { Title } = Typography

	useEffect(() => {
		/** Check local storage */
		const darkModeStorage = localStorage.getItem('darkMode')
		if (darkModeStorage === 'true') {
			setDarkMode(true)
		} else if (darkModeStorage === 'false') {
			setDarkMode(false)
		}
	})
	return (
		<div className={styles.container}>
			<Card>
				<Title level={2} className={styles.title}>
					Scout
				</Title>
				<Typography>Analyze VCFs quicker and easier</Typography>
				<Divider className={styles.divider} />
				<HomeDescription />
				<Typography className={styles.version} data-testid="version">
					Version: {scoutVersion}
				</Typography>
			</Card>
			<div className={styles.logosContainer}>
				<img
					className={styles.karolinskaLogo}
					src={`${settings.darkMode ? KarolinskaLogoDark : KarolinskaLogo}`}
					alt="Karolinska Logo"
				/>

				<img className={styles.swedacLogo} src={SwedacLogo} alt="Swedac Logo" />

				<img
					className={styles.sciLifeLabLogo}
					src={`${settings.darkMode ? ScilifelabLogoDark : ScilifelabLogo}`}
					alt="Scilifelab Logo"
				/>
			</div>
		</div>
	)
}

export const Home = connect(mapState, mapDispatch)(HomePage)
