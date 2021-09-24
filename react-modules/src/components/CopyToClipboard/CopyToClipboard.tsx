import React from 'react'
import { Button } from 'antd'
import { CopyOutlined } from '@ant-design/icons'
import { ErrorNotification, SuccessNotification } from 'services/helpers/helpers'

export default function CopyToClipboard({ copiedData }: { copiedData: any[] }) {
	const addToClipboard = (copiedData: any[]) => {
		if (copiedData === undefined || copiedData.length == 0) {
			ErrorNotification({
				type: 'error',
				message: 'Copy failed!',
				description: 'There is no data to copy!',
			})
		} else {
			const dummy = document.createElement('textarea')
			document.body.appendChild(dummy)
			dummy.value =
				'Exported data \n\nHPO term	Phenotype description\tNumber of associated genes \n\n'
			copiedData.map((data) => {
				dummy.value += data.hpo_id + '\t' + data.description + '\t' + data.genes.length + '\n'
			})
			dummy.select()
			document.execCommand('copy')
			document.body.removeChild(dummy)
			SuccessNotification({
				type: 'success',
				message: 'Copy successful!',
				description: `Copied ${copiedData.length} row${
					copiedData.length == 1 ? '' : 's'
				} to clipboard!`,
			})
		}
	}
	return (
		<div>
			<Button type="primary" icon={<CopyOutlined />} onClick={(e) => addToClipboard(copiedData)}>
				Copy to clipboard
			</Button>
		</div>
	)
}
