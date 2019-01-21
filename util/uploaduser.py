from orm.user import User, session


def upload_users_from_file(file_='./userlist.csv'):
    column = ('account', 'passwd', 'country')
    for line in open(file_).readlines():
        values = line.split()
        print(values)
        mapping = zip(column, values)
        kwargs = dict(mapping)
        user = User(**kwargs)
        session.add(user)

    session.commit()


if __name__ == '__main__':
    upload_users_from_file()
