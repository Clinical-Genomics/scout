import React from "react";
import { Link } from "react-router-dom";
import styles from "./Nav.module.scss";
import DropdownMenu from "components/DropdownMenu/DropdownMenu";

export interface Header {
  icon?: string; // Path to icon
  title?: string; // Name of webpage
}

export interface NavItem {
  linkTitle: string;
  public: boolean;
  link?: string;
  dropdownList?: Array<NavItem>;
}

interface Props {
  header?: Header;
  navItems: Array<NavItem>;
}

const Nav: React.FC<Props> = ({ header, navItems }) => {
  return (
    <nav className={styles.Nav}>
      <ul>
        {/* Header */}
        {header?.icon && header?.title && (
          <li key={header.title}>
            <header>
              <Link to="/" className={styles.header}>
                {header?.icon && <img src={header.icon} alt="Logo" />}
                {header?.title && <span>{header.title}</span>}
              </Link>
            </header>
          </li>
        )}

        {/* Nav items */}
        {navItems.map((navItem) => (
          <li key={navItem.linkTitle}>
            {/* Link */}
            {navItem.link && <Link to={navItem.link}>{navItem.linkTitle}</Link>}

            {/* Dropdown menu */}
            {navItem.dropdownList && (
              <>
                <span className={"no-button-style"}>
                  {navItem.linkTitle}
                  {" v"}
                </span>

                <DropdownMenu>
                  {navItem.dropdownList.map((dropDownItem) => (
                    <li key={dropDownItem.linkTitle}>
                      <Link to={dropDownItem.link ? dropDownItem.link : "/"}>
                        {dropDownItem.linkTitle}
                      </Link>
                    </li>
                  ))}
                </DropdownMenu>
              </>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Nav;
