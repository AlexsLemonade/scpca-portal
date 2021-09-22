import React from 'react'
import { Blank } from 'grommet-icons'
import Check from '../images/check.svg'
import ChevronDown from '../images/chevron-down.svg'
import ChevronLeft from '../images/chevron-left.svg'
import ChevronRight from '../images/chevron-right.svg'
import ChevronUp from '../images/chevron-up.svg'
import Cite from '../images/cite.svg'
import Cross from '../images/cross.svg'
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

export const SVGs = {
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Cite,
  Cross,
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
  Warning
}

export const Icon = ({ color = 'brand', size = 'medium', name }) => {
  const IconSVG = SVGs[name]
  return (
    <Blank color={color} size={size}>
      <IconSVG />
    </Blank>
  )
}

export default Icon
