import React, { useState } from 'react'
import styles from './Phenotypes.module.css'
import { Input, Space } from 'antd'
import { PhenotypesTable } from '../../components/PhenotypesTable/PhenotypesTable'
import { getPhenotypes } from 'services/ScoutApi'
import { ExportCSV } from 'components/ExportCSV/ExportCSV'
import CopyToClipboard from 'components/CopyToClipboard/CopyToClipboard'

const { Search } = Input
export const PhenotypesPage = () => {
	const [phenotypes, setPhenotypes] = useState<any>()
	const onSearch = (value: any) => {
		if (value != '') {
			// The Mirage.js dose not support search
			getPhenotypes().then((response: any) => {
				setPhenotypes(response)
			})
		}
	}
	return (
		<div className={styles.container} data-testid="phenotypes">
			<div className={styles.header} data-testid="test-phenotypes">
				<div className={styles.buttons}>
					<Space size="middle">
						<ExportCSV csvData={phenotypes} fileName={'scout_phenotypes'} />
						<CopyToClipboard copiedData={phenotypes} />
					</Space>
				</div>
				<Search
					placeholder="Search penotypes ..."
					onSearch={onSearch}
					enterButton="Search"
					style={{ width: '30vw' }}
				/>
			</div>
			{phenotypes && (
				<div>
					<PhenotypesTable phenotypes={phenotypes} />
				</div>
			)}
		</div>
	)
}
