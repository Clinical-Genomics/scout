import { Notification } from '../interfaces'
import { notification } from 'antd'

export const ErrorNotification = ({ type, message, description }: Notification) => {
  const key = `open${Date.now()}`
  notification[type]({
    message,
    description,
    btn: null,
    key,
    closeIcon: null,
    duration: 0,
  })
}

export const SuccessNotification = ({ type, message, description }: Notification) => {
  const key = `open${Date.now()}`
  notification[type]({
    message,
    description,
    btn: null,
    key,
    closeIcon: null,
    duration: 2,
  })
}
