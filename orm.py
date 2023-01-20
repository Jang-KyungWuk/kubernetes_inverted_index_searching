from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

class DB:
    # 테이블 구조 정의
    base = declarative_base()

    class Test(base):
        __tablename__="test_table"
        t_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
        t_text = Column(VARCHAR(500))
        
    class D2K(base):
        __tablename__="doc2key_table"
        d_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
        d_d2k = Column(VARCHAR(1000))
    
    class K2D(base):
        __tablename__="key2doc_table"
        k_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
        k_kwd = Column(VARCHAR(40))
        k_k2d = Column(VARCHAR(1000))
    
    
    def test_view_by_ids(self,ids):
        returnData = ""
        q = self.session.query(self.Test).filter(self.Test.t_id.in_(ids))
        for l in q:
            ls = "%s %s\n"%(l.t_id,l.t_text)
            print(ls, end="")
            returnData+=ls
        return returnData
    
    def test_view(self):
        returnData = ""
        q = self.session.query(self.Test)
        for l in q:
            ls = "%s %s\n"%(l.t_id,l.t_text)
            print(ls, end="")
            returnData+=ls
        return returnData
    
    def return_search_kwd(self):
        returnData = ""
        q = self.session.query(self.K2D)
        for l in q:
            ls = ('%s\n'%l.k_kwd)
            print(ls, end="")
            returnData+=ls
        return returnData
    
    def test_add(self, testText):
        self.session.add(self.Test(t_text=testText))
        searchableKwds = self.searchable(testText, self.session.query(self.Test)[-1].t_id)
        self.session.commit()
        return searchableKwds
    
    def searchable(self, testText, cid):
        kwds = self.ngram_spliter(testText)
        kwdSet = set()
        for kwd in kwds:
            print(kwd)
            q = self.session.query(self.K2D).filter(self.K2D.k_kwd == kwd).first()
            if q:
                k2d = q.k_k2d
                if '+%s+'%cid not in k2d:
                    k2d+='%s+'%cid
                    q.k_k2d = k2d
            else:
                self.session.add(self.K2D(k_kwd=kwd,
                                          k_k2d='+%s+'%cid))
            try:
                ckid = q.k_id
            except:
                ckid = self.session.query(self.K2D).filter(self.K2D.k_kwd == kwd).first().k_id
            kwdSet.add(ckid)
        
        strKwdSet = str(kwdSet)[1:-1].replace(', ','+')
        self.session.add(self.D2K(d_d2k=strKwdSet))
        
        return str(kwds)[1:-1]
    
    def ngram_spliter(self, fulltext):
        fulltext = fulltext.replace('\n',' ')
        idxSet=set()
        segments = set(fulltext.split(' '))

        for segment in segments:
            segLen = len(segment)
            for idxLen in range(1,segLen+1):
                for cursor in range(0,segLen-idxLen+1):
                    idxSet.add(segment[cursor:cursor+idxLen])
        return idxSet

    def search(self,kwds):
        try:
            kwdSplit = kwds.split(' ')
            target = set(list(map(int,self.session.query(self.K2D).filter(self.K2D.k_kwd == kwdSplit[0]).first().k_k2d[1:-1].split('+'))))
            for kwdCursor in range(1,len(kwdSplit)):
                target = target.intersection(list(map(int,self.session.query(self.K2D).filter(self.K2D.k_kwd == kwdSplit[kwdCursor]).first().k_k2d[1:-1].split('+'))))
                if len(target)==0:
                    return ""
            return self.test_view_by_ids(target)
        except:
            return ""
    
    
    # 엔진 생성
    def create_engine_from_port(self,port,dbProtocol,dbPwd,dbContainerAddress):
        return create_engine("%s://%s@%s:%s"%(dbProtocol,dbPwd,dbContainerAddress,port), echo=False)
    
    # 세션 생성
    def create_session(self,engine):
        Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)
        session = Session()
        return session

    def create_DB(self):
        self.base.metadata.create_all(self.engine)
        self.session.commit()
    
    
    def htmlfy(self,text, highlights=[]):
        text = text.replace('\n','<br/>')
        for highlight in highlights:
            text = text.replace(highlight,'<b>%s</b>'%highlight)
        return text
        
    
    # 인스턴스 생성 시 localhost 포트에 대한 엔진, 세션 인스턴스를 생성
    def __init__(self,port,
                 dbProtocol='postgresql',dbPwd='postgres:postgrespw',dbContainerAddress='localhost',
                 initialValue='local'):    
        
        if initialValue in ['Docker','docker','container','Container','도커','컨테이너']:
            # 기본값과 다른 값이 입력되어을때만 변경
            if dbProtocol == 'postgresql':
                dbProtocol = 'postgresql+psycopg2'
            if dbPwd == 'postgres:postgrespw':
                dbPwd = 'postgres:postgrespw'
            if dbContainerAddress == 'localhost':
                dbContainerAddress = '172.17.0.1'
        
        self.engine=self.create_engine_from_port(port,dbProtocol,dbPwd,dbContainerAddress)
        self.session=self.create_session(self.engine)
        self.create_DB()
