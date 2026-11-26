import Link from "next/link";

import { AccountMenu } from "@/components/layout/account-menu";
import { NavLinks } from "@/components/layout/nav-links";
import { buttonClassName } from "@/components/ui/styles";
import { getCurrentUser } from "@/lib/auth/session";

/** The right part of the header: the app's sections once logged in, else sign in links. */
export async function UserMenu() {
  const user = await getCurrentUser();

  if (!user) {
    return (
      <div className="ml-auto flex items-center gap-2">
        <Link href="/login" className={buttonClassName("ghost")}>
          Log in
        </Link>
        <Link href="/register" className={buttonClassName("primary")}>
          Sign up
        </Link>
      </div>
    );
  }

  return (
    <>
      {/* On small screens the sections wrap onto their own row, under the logo */}
      <div className="order-last -mx-1 w-full md:order-none md:mx-0 md:w-auto md:flex-1">
        <NavLinks />
      </div>
      <div className="ml-auto">
        <AccountMenu user={user} />
      </div>
    </>
  );
}
