import pandas as pd
from pandas import DataFrame

class CfbDataManager(DataFrame):
    def __init__(self, df, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in df:
            if "Unnamed" in key: continue
            self[key] = df[key]
        if 'id' in self: self.set_index('id',inplace=True)
    @classmethod
    def from_file(cls,file_name,*args, **kwargs):
        df = pd.read_csv(file_name)
        return cls(df,*args, **kwargs)
    def teams(self):
        return pd.concat([self['home_team'],self['away_team']]).unique()
    def view(self,**kwargs):
        df = self
        for key in kwargs:
            if key == "team": 
                df = df[(df['home_team']==kwargs[key]) | (df['away_team']==kwargs[key])]   
                continue
            assert key in df, "key {} not in dataframe".format(key)
            df = df[df[key]==kwargs[key]]
        return self.__class__(df)
    def occured_games(self):
        return self.__class__(self[(self['home_points'] > 0) & (self['away_points'] > 0)])
    def combine(self,df):
        if 'id' in df: df = df.set_index("id")
        assert df.index.name == "id", "index must be id"
        self = self[~self.index.isin(df.index)]
        df3 = pd.concat([self,df])
        return self.__class__(df3)
    def teams_and_scores(self):
        columns = ['away_team', 'home_team','away_points', 'home_points', 'neutral_site']
        return self.__class__(self[columns])
    def get_data(self,api_key,season,**kwargs):
        import cfbd
        from cfbd.rest import ApiException
        # Configure API key authorization: ApiKeyAuth
        configuration = cfbd.Configuration()
        configuration.api_key['Authorization'] = api_key
        configuration.api_key_prefix['Authorization'] = 'Bearer'
        # create an instance of the API class
        api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
        games = api_instance.get_games(season, season_type='regular', **kwargs)
        games+=api_instance.get_games(season, season_type='postseason', **kwargs)
        games = [game.to_dict() for game in games]
        df = pd.DataFrame(games)
        return self.combine(df)
