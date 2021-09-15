import React from 'react'
import { Table } from 'antd'

interface PhenotypesTableProps {
	phenotypes: any[]
}

const columns = [
	{
		title: 'HPO term',
		dataIndex: 'hpo_id',
		key: '_id',
		render: (name: string) => (
			<a
				href={`http://hpo.jax.org/app/browse/term/${name}`}
				target="_blank"
				rel="noopener noreferrer"
			>
				{name}
			</a>
		),
	},
	{
		title: 'Phenotype description',
		dataIndex: 'description',
		key: '_id',
	},
	{
		title: 'Number of associated genes',
		dataIndex: 'genes',
		key: '_id',
	},
]

export const PhenotypesTable = ({ phenotypes }: PhenotypesTableProps) => {
	return (
		<Table bordered columns={columns} dataSource={phenotypes} pagination={false} rowKey={'_id'} />
	)
}
