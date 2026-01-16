'use client'

import { Link } from '@/lib/api'
import {
  Mail,
  Phone,
  MessageCircle,
  Linkedin,
  Twitter,
  Instagram,
  Facebook,
  Youtube,
  Github,
  Globe,
  ExternalLink,
} from 'lucide-react'

interface LinkButtonProps {
  link: Link
  primaryColor: string
  textColor: string
  onClick: () => void
}

const getLinkIcon = (linkType: string) => {
  const iconProps = { size: 20 }

  switch (linkType.toLowerCase()) {
    case 'email':
      return <Mail {...iconProps} />
    case 'phone':
      return <Phone {...iconProps} />
    case 'whatsapp':
      return <MessageCircle {...iconProps} />
    case 'linkedin':
      return <Linkedin {...iconProps} />
    case 'twitter':
      return <Twitter {...iconProps} />
    case 'instagram':
      return <Instagram {...iconProps} />
    case 'facebook':
      return <Facebook {...iconProps} />
    case 'youtube':
      return <Youtube {...iconProps} />
    case 'github':
      return <Github {...iconProps} />
    case 'website':
      return <Globe {...iconProps} />
    default:
      return <ExternalLink {...iconProps} />
  }
}

export default function LinkButton({
  link,
  primaryColor,
  textColor,
  onClick,
}: LinkButtonProps) {
  const handleClick = () => {
    onClick()
    window.open(link.url, '_blank', 'noopener,noreferrer')
  }

  return (
    <button
      onClick={handleClick}
      className="w-full py-4 px-6 rounded-lg font-semibold transition-all duration-200 hover:scale-105 hover:shadow-lg flex items-center justify-center gap-3"
      style={{
        backgroundColor: primaryColor,
        color: '#ffffff',
      }}
    >
      {getLinkIcon(link.link_type)}
      <span>{link.title}</span>
    </button>
  )
}
