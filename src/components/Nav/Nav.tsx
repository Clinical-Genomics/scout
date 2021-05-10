import React, { useState } from "react";
import { Link } from "react-router-dom";
import { GoogleLogin, GoogleLogout } from "react-google-login";
import styles from "./Nav.module.scss";
import DropdownMenu from "components/DropdownMenu/DropdownMenu";
import { FaAngleDown, FaMoon, FaRegSun } from "react-icons/fa";

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
  darkMode: boolean;
  toggleDarkMode: Function;
}

const { REACT_APP_GOOGLE_OAUTH_CLIENT_ID } = process.env;
const clientId = REACT_APP_GOOGLE_OAUTH_CLIENT_ID
  ? REACT_APP_GOOGLE_OAUTH_CLIENT_ID
  : "no-id";

const Nav: React.FC<Props> = ({
  header,
  navItems,
  darkMode,
  toggleDarkMode,
}) => {
  const [userName, setUserName] = useState("");
  const [sigendIn, setSigendIn] = useState(false);

  const responseGoogle = (response: any) => {
    setUserName(response.ft.Ue);
    setSigendIn(true);
  };

  const onLogoutSuccess = () => {
    setSigendIn(false);
  };

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
                <span>
                  {navItem.linkTitle}
                  <FaAngleDown className={styles.collapse_arrow} />
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
      <ul>
        <li>
          <button
            className="no_button_style flex"
            onClick={() => toggleDarkMode()}
          >
            {darkMode && <FaMoon />}
            {!darkMode && <FaRegSun />}
          </button>
        </li>
        {/* Greeting */}
        {sigendIn && (
          <li key={"logout"} className={styles.greeting}>
            <span>
              {`Hi ${userName}!`}
              <FaAngleDown className={styles.collapse_arrow} />
            </span>
            <DropdownMenu>
              <li>
                <GoogleLogout
                  clientId={clientId}
                  render={(renderProps) => (
                    <button
                      className={"no_button_style"}
                      onClick={renderProps.onClick}
                      disabled={renderProps.disabled}
                    >
                      Sign out
                    </button>
                  )}
                  buttonText="Sign out"
                  onLogoutSuccess={onLogoutSuccess}
                />
              </li>
            </DropdownMenu>
          </li>
        )}
        {/* Login button */}
        {!sigendIn && (
          <li>
            <GoogleLogin
              clientId={clientId}
              render={(renderProps) => (
                <button
                  className={`${styles.login_button} btn-style`}
                  onClick={renderProps.onClick}
                  disabled={renderProps.disabled}
                >
                  Login with Google
                </button>
              )}
              buttonText="Login"
              onSuccess={responseGoogle}
              onFailure={responseGoogle}
              isSignedIn={true}
              cookiePolicy={"single_host_origin"}
            />
          </li>
        )}
      </ul>
    </nav>
  );
};

export default Nav;
