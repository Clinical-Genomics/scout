import React from 'react'
import { Table, Tag } from 'antd'

interface CasesTableProps {
	cases: any[]
}

const columns = [
	{
		title: 'Name',
		dataIndex: 'display_name',
		key: 'display_name',
		render: (name: string) => <a href={`${window.location.href.slice(0, -5)}${name}`}>{name}</a>,
	},
	{
		title: 'Status',
		dataIndex: 'status',
		key: 'status',
	},
	{
		title: 'Analysis date',
		dataIndex: 'analysis_date',
		key: 'analysis_date',
		render: (date: string) => <div>{new Date(date).toISOString().slice(0, 10)}</div>,
	},
	{
		title: 'Link',
		key: 'tags',
		dataIndex: 'tags',
	},
	{
		title: 'Sequencing',
		dataIndex: 'analysis_types',
		key: 'analysis_types',
		render: (analysisTypes: string[]) => (
			<div>
				{analysisTypes.map((analysisType) => (
					<Tag color={'blue'} key={analysisType}>
						{analysisType}
					</Tag>
				))}
			</div>
		),
	},
	{
		title: 'Track',
		key: 'track',
	},
]

export const CasesTable = ({ cases }: CasesTableProps) => {
	return (
		<Table
			bordered
			columns={columns}
			dataSource={cases}
			pagination={false}
			rowKey={'display_name'}
		/>
	)
}
