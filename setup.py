from setuptools import setup

setup(name="dublinpengpeng",
      version="0.1",
      description="for DublinBikePro",
      url="",
      author="pengpeng group",
      author_email="yi.zhang2@ucdconnect.ie",
      licence="GPL3",
      packages=['dublinpengpeng'],
      entry_points={
        'console_scripts':['dublinbike_group=dublinpengpeng.JsontoMysql:main']
        }
      )
