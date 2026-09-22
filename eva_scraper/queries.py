LOGIN_MUTATION = """
query login($email: String!, $password: String!, $otp: String) {
  login(email: $email, password: $password, otp: $otp) {
    ...AuthTokenFields
    user {
      role
      locations {
        id
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment AuthTokenFields on AuthToken {
  accessToken
  user {
    ...UserFields
    __typename
  }
  __typename
}

fragment UserFields on User {
  ...UserMinimalFields
  referralCode
  email
  emailConfirmed
  createdAt
  role
  gender
  phone
  birthdate
  firstName
  lastName
  fullName
  address {
    line1
    postalCode
    city
    country
    state
    __typename
  }
  language
  newsletter
  isPublic
  isPasswordConfigured
  abilities
  eSportEnabled
  eSportExpiresAt
  eSportLocationIdList
  usernameToken
  authorization {
    ...AuthorizationFields
    __typename
  }
  __typename
}

fragment UserMinimalFields on User {
  id
  username
  displayName
  fullName
  __typename
}

fragment AuthorizationFields on Authorization {
  actions
  __typename
}
"""

REFRESH_TOKEN_MUTATION = """
mutation refreshToken {
  refreshToken {
    accessToken
    __typename
  }
}
"""
