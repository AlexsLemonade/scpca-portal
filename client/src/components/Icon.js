import React from 'react'
import { Text } from 'grommet'
import { Blank } from 'grommet-icons'
import Check from '../images/check.svg'
import ChevronDown from '../images/chevron-down.svg'
import ChevronLeft from '../images/chevron-left.svg'
import ChevronRight from '../images/chevron-right.svg'
import ChevronUp from '../images/chevron-up.svg'
import Cite from '../images/cite.svg'
import Cross from '../images/cross.svg'
import Download from '../images/download.svg'
import Dropdown from '../images/dropdown.svg'
import Edit from '../images/edit.svg'
import Filter from '../images/filter.svg'
import Gear from '../images/gear.svg'
import Help from '../images/help.svg'
import Info from '../images/info.svg'
import MoreOptions from '../images/more-options.svg'
import Plus from '../images/plus.svg'
import Search from '../images/search.svg'
import Trashcan from '../images/trash-can.svg'
import View from '../images/view.svg'
import Warning from '../images/warning.svg'
import WarningNoFill from '../images/warning-no-fill.svg'
import Twitter from '../images/twitter.svg'
import Facebook from '../images/facebook.svg'
import Instagram from '../images/instagram.svg'
import Github from '../images/github.svg'
import Copy from '../images/copy.svg'

export const SVGs = {
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Cite,
  Copy,
  Cross,
  Download,
  Dropdown,
  Edit,
  Filter,
  Gear,
  Help,
  Info,
  MoreOptions,
  Plus,
  Search,
  Trashcan,
  View,
  Warning,
  WarningNoFill,
  Twitter,
  Instagram,
  Facebook,
  Github,
  htmlGear: '⚙️'
}

export const Icon = ({ color = 'brand', size = 'medium', name }) => {
  const IconContent = SVGs[name]

  return typeof IconContent === 'string' ? (
    <Text aria-hidden="true" size={size}>
      {IconContent}
    </Text>
  ) : (
    <Blank color={color} size={size}>
      <IconContent />
    </Blank>
  )
}

export default Icon
