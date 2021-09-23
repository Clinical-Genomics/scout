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
    sorter: (a: any, b: any) => {
      if (a.hpo_id && b.hpo_id) {
        return a.hpo_id.localeCompare(b.hpo_id)
      }
      return 0
    },
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
    sorter: (a: any, b: any) => a?.genes?.length - b?.genes?.length,
    render: (genes: string) => <span>{genes.length}</span>,
  },
]

export const PhenotypesTable = ({ phenotypes }: PhenotypesTableProps) => {
  return (
    <Table
      bordered
      columns={columns}
      dataSource={phenotypes}
      rowKey={'_id'}
      expandIconColumnIndex={-1}
      pagination={false}
    />
  )
}
