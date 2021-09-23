import React from 'react'
import { Spin } from 'antd'

export const Loading = () => {
  return (
    <Spin
      size="large"
      style={{
        position: 'fixed',
        zIndex: 2,
        top: '50%',
        left: '50%',
      }}
    />
  )
}
